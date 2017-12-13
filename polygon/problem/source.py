import subprocess
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView
from os import path, makedirs

from polygon.models import RepositorySource
from polygon.problem.exception import RepositoryException
from polygon.problem.forms import SourceEditForm
from polygon.problem.sync import sync_problem_to_servers
from polygon.problem.utils import LANG_CONFIG
from polygon.problem.views import PolygonProblemMixin
from problem.models import SpecialProgram
from utils import random_string
from utils.hash import file_hash, code_hash


class SourceListView(PolygonProblemMixin, ListView):
    template_name = 'polygon/problem/source_list.jinja2'
    context_object_name = 'source_list'

    def get_queryset(self):
        return self.problem.repositorysource_set.all()

    def get_select_list(self, t):
        ret = [('', 'None')]
        ret += map(lambda x: (x.name, x.name), self.problem.repositorysource_set.filter(tag=t))
        ret += map(lambda x: (x.fingerprint, x.filename + ' (builtin)'),
                   SpecialProgram.objects.filter(builtin=True, category=t).order_by('filename'))
        return ret

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['checkers'] = self.checker_list = self.get_select_list('checker')
        data['validators'] = self.validator_list = self.get_select_list('validator')
        data['interactors'] = self.interactor_list = self.get_select_list('interactor')
        return data

    def post(self, *args, **kwargs):
        # I don't know why this is here. This post is to select checker and etc. for a problem
        ts = ['checker', 'validator', 'interactor']
        try:
            for t in ts:
                fingerprint = self.request.POST.get(t, '')
                if fingerprint == '':
                    setattr(self.problem, t, '')
                    continue
                if not SpecialProgram.objects.filter(fingerprint=fingerprint).exists():
                    file_name = fingerprint
                    source = self.problem.repositorysource_set.get(name=file_name)
                    fingerprint = code_hash(source.code, source.lang)
                    if not SpecialProgram.objects.filter(fingerprint=fingerprint).exists():
                        SpecialProgram.objects.create(fingerprint=fingerprint, lang=source.lang, filename=file_name,
                                                      code=source.code, category=t)
                setattr(self.problem, t, fingerprint)
            sync_problem_to_servers(self.problem)
            self.problem.save(update_fields=ts)
        except KeyError:
            raise RepositoryException("Post info not complete")
        except RepositorySource.DoesNotExist as e:
            raise RepositoryException(str(e))
        return redirect(self.request.path)


class SourceCreateView(PolygonProblemMixin, CreateView):
    template_name = 'polygon/problem/source_edit.jinja2'
    form_class = SourceEditForm

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.author = self.request.user
        instance.workspace = random_string()
        instance.problem = self.problem
        Program(instance).compile()
        instance.save()
        return redirect(reverse('polygon:repo_source_list', kwargs=self.kwargs))

    def get_success_url(self):
        return self.request.path


class SourceEditView(PolygonProblemMixin, UpdateView):
    template_name = 'polygon/problem/source_edit.jinja2'
    form_class = SourceEditForm

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.workspace = random_string()
        Program(instance).compile()
        instance.save()
        return redirect(self.get_success_url())

    def get_object(self, queryset=None):
        return RepositorySource.objects.get(pk=self.kwargs['source'], problem_id=self.problem.pk)

    def get_success_url(self):
        return self.request.path


class Program:

    MAX_READ_SIZE = 2048

    @staticmethod
    def split_and_format_command(cmd, **kwargs):
        ret = []
        for x in cmd.split():
            ret.append(x.format(**kwargs))
        return ret

    def __init__(self, source: RepositorySource):
        self.source = source
        try:
            _config = LANG_CONFIG[self.source.lang]
            self.workspace = path.join(settings.REPO_DIR, str(source.problem_id), 'source', self.source.workspace)
            makedirs(self.workspace, exist_ok=True)
            self.code_path = path.join(self.workspace, _config['codeFile'])
            self.exe_path = path.join(self.workspace, _config['exeFile'])
            self.compiler_command = self.split_and_format_command(_config["compilerCmd"],
                                                                  workspace=self.workspace, code_path=self.code_path,
                                                                  exe_path=self.exe_path)
            self.execute_command = self.split_and_format_command(_config["executeCmd"],
                                                                 workspace=self.workspace, code_path=self.code_path,
                                                                 exe_path=self.exe_path)
        except KeyError:
            raise RepositoryException("Unrecognized language.")

    def compile(self):
        try:
            with open(self.code_path, 'w') as code_file:
                code_file.write(self.source.code)
            pr = subprocess.run(self.compiler_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            if pr.returncode != 0:
                # something is wrong
                raise RepositoryException(pr.stdout.decode() or pr.stderr.decode())
        except subprocess.TimeoutExpired:
            raise RepositoryException("Compilation time limit exceeded.")
        except FileNotFoundError:
            raise RepositoryException("Compiler not found. Contact admin.")

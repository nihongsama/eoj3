if (window.hasOwnProperty("ace")) {
  var map = {
    'c': 'c_cpp',
    'c11': 'c_cpp',
    'cpp98': 'c_cpp',
    'cpp': 'c_cpp',
    'cpp14': 'c_cpp',
    'csharp': 'csharp',
    'python2': 'python',
    'python': 'python',
    'java': 'java',
    'php': 'php',
    'fortran': 'fortran',
    'perl': 'perl',
    'ruby': 'ruby',
    'objc': 'objectivec',
    'haskell': 'haskell',
    'scala': 'scala',
    'lua': 'lua',
    'lisp': 'lisp',
    'js': 'javascript',
    'go': 'golang',
    'ocaml': 'ocaml',
    'fsharp': 'text',
    'pypy2': 'python',
    'swift': 'swift',
    'pascal': 'pascal',
    'rust': 'rust',
    'r': 'r'
  };
  var editor = ace.edit("editor");
  var lang = $("#id_lang");
  var code = $("#id_code");
  editor.getSession().setValue(code.val());
  editor.setTheme("ace/theme/chrome");
  editor.getSession().setMode("ace/mode/" + map[lang.val()]);
  editor.setOptions({
    fontFamily: "Courier",
    fontSize: "11pt"
  });
  lang.on("change", function (event) {
    editor.getSession().setMode("ace/mode/" + map[event.target.value]);
  });
  editor.getSession().on("change", function () {
    code.val(editor.getSession().getValue());
  });
}

function scrollToCurrentSubmission () {
  $('html, body').animate({
    scrollTop: $("#current-submission").offset().top - $("#navbar").height() - 15
  }, 500);
}

function updateSubmission (url) {
  $.get(url, function (data) {
    var submissionBox = $("#current-submission");
    submissionBox.html(data);
    var status = submissionBox.find(".status-span.with-icon").attr("data-status");
    if (status == "-3" || status == "-2") {
      setTimeout(function() {
        updateSubmission(url);
      }, 500);
    } else {
      updatePastSubmissions();
    }
    $.parseStatusDisplay();
  });
}

function updatePastSubmissions () {
  var pastSubmissionBox = $("#past-submissions");
  if (pastSubmissionBox.length > 0) {
    $.get(pastSubmissionBox.data("url"), function (data) {
      pastSubmissionBox.html(data);
      $.parseStatusDisplay();
    });
  }
}

$("#problem-submit").click(function (event) {
  var button = $(event.currentTarget);
  var form = button.closest("form");
  form.addClass("loading");
  $.post(form.attr("action"), form.serialize(), function (data) {
    updateSubmission(data.url);
    form.removeClass("loading");
    scrollToCurrentSubmission();
  }, "json");
  return false;
});

updatePastSubmissions();
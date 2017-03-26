/**
 * Basic app that shows some examples and lets the user
 * interact with the compiler live.
 * 
 * Juan Pablo de la Cruz Gutierrez
 */
require.config({
  baseUrl: '',

  paths: {
    d3: "libs/d3/build/d3.min",
    katex: "libs/katex/dist/katex.min"
  },
  shims: {
    'd3': {
      exports: 'd3'
    }
  },
  /** refer to the documentation of codemirror
   * to see why it has to be imported this way */
  packages: [{
    name: 'codemirror',
    location: 'libs/codemirror',
    main: 'lib/codemirror'
  },
  {
    name: 'troff',
    location: 'libs/codemirror',
    main: 'mode/troff/troff'
  }]
});

requirejs(['d3',
  'codemirror',
  'katex'],
  function (d3, CodeMirror, KaTeX) {
    'use strict;';

    var table = d3.select('body')
      .append('div')
      .classed('table', true),
      row = table.append('div')
        .classed('tableRow', true);
    row.append('div')
      .classed('tableCell', true)
      .attr('id', 'editor');
    row.append('div')
      .classed('tableCell', true)
      .attr('id', 'output');

    newrow = table.append('div')
      .classed('tableRow', true);
    newrow.append('div')
      .classed('tableCell', true)
      .html('Type in your eqn expression...');
    newrow.append('div')
      .classed('tableCell', true)
      .html('and see how it is compiled into LaTeX');

    var head = document.getElementsByTagName('head')[0],
      script = document.createElement('script');

    // Add a web worker which takes edits, and finally send the final edit
    // when he has emptied the queue or told to finish.
    // var worker = new Worker('src/liveeditor.js');
    // worker.onmessage = function (event) {
    //   d3.select('#output')
    //     .html(event.data);
    // };

    // window.addEventListener("beforeunload", function () {
    //   worker.terminate();
    // });

    script.src = "libs/codemirror/mode/troff/troff.js";
    script.onload = function () {
      var myCodeMirror = CodeMirror(d3.select('#editor').node(), {
        value: "x over 2",
        mode: "troff",
        theme: "dracula"
      });

      function parseEqn(data) {
        // show current status
        // worker.postMessage(data.getValue());
        d3.request('http://localhost:5000/eqn?expr=' + data.getValue())
          .get(function (latex) {
            d3.select('#output')
              .html(KaTeX.renderToString(latex.response));
          });
      }

      myCodeMirror.on('changes', parseEqn);
      parseEqn(myCodeMirror);

      // start the worker
      // worker.postMessage("");
    };
    head.appendChild(script);
  });
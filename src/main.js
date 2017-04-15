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
    katex: "libs/katex/dist/katex.min",
    es6promise: "libs/es6-promise/es6-promise.min"
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
  'katex',
  'es6promise'],
  function (d3, CodeMirror, KaTeX, es6promise) {
    'use strict;';

    var Promise = es6promise.Promise;

    var table = d3.select('#container')
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

    // Add some documentation and examples to get people going. encodeURI
    var examples = ['x over 2', '{ x + 2 } over { y sup 2 + 1 }'],
      doctbl = d3.select('#container')
        .append('div')
        .classed('table', true)
        .attr('id', 'examples');

    // Evaluate all examples asynchronously and get the results in an array.
    Promise.all(examples.map(function (expression) {
      return new Promise(function (resolve, reject) {
        d3.request(window.location.href + 'eqn?expr=' + encodeURIComponent(expression))
          .get(function (latex) {
            resolve(KaTeX.renderToString(latex.response));
          })
          .on('error', function (err) {
            reject(err);
          });
      });
    })).then(function (latex) {
      var exow = doctbl
        .selectAll('div')
        .data(examples).enter()
        .append('div')
        .classed('tableRow', true)
        .selectAll('div')
        .data(function (expr, i) {
          return [expr, latex[i]];
        }).enter()
        .append('div')
        .classed('tableCell', true)
        .classed('eqncell', true)
        .html(function (d) {
          return d;
        });
    });

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

    var head = document.getElementsByTagName('head')[0],
      script = document.createElement('script');
    script.src = "libs/codemirror/mode/troff/troff.js";
    script.onload = function () {
      var myCodeMirror = CodeMirror(d3.select('#editor').node(), {
        value: "int from 0 to inf pi (x)dx",
        mode: "troff",
        theme: "dracula"
      });

      function parseEqn(data) {
        var request = encodeURIComponent(data.getValue());
        // worker.postMessage(data.getValue());
        d3.request(window.location.href + 'eqn?expr=' + request)
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

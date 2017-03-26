/**
 * Worker taking care of evaluating the eqn code.
 */

self.importScripts('../libs/d3/build/d3.min.js');

// just send back the data
self.addEventListener('message', function (e) {
  // self.postMessage(e.data);
  if (e.data) {
    var worker = self;
    d3.request('http://localhost:5000/eqn?expr=' + e.data)
      .get(function (latex) {
        worker.postMessage(latex);
      });
  }
});
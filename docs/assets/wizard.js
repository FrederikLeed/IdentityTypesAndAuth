/* Identity-selection wizard */
/* eslint-disable */

(function () {
  "use strict";

  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      for (var k in attrs) {
        if (k === "className") node.className = attrs[k];
        else if (k === "onClick") node.addEventListener("click", attrs[k]);
        else if (k === "html") node.innerHTML = attrs[k];
        else if (attrs[k] != null) node.setAttribute(k, attrs[k]);
      }
    }
    if (children) {
      (Array.isArray(children) ? children : [children]).forEach(function (c) {
        if (c == null) return;
        if (typeof c === "string") node.appendChild(document.createTextNode(c));
        else node.appendChild(c);
      });
    }
    return node;
  }

  function Wizard(rootId, data) {
    this.root = document.getElementById(rootId);
    if (!this.root) return;
    this.data = data;
    this.s = data.strings;
    this.history = [];
    this.start();
  }

  Wizard.prototype.start = function () {
    this.history = [this.data.startId];
    this.render();
  };

  Wizard.prototype.go = function (nodeId) {
    if (!nodeId) return;
    this.history.push(nodeId);
    this.render();
  };

  Wizard.prototype.back = function () {
    if (this.history.length > 1) {
      this.history.pop();
      this.render();
    }
  };

  Wizard.prototype.currentNode = function () {
    var id = this.history[this.history.length - 1];
    return this.data.nodes[id];
  };

  Wizard.prototype.render = function () {
    while (this.root.firstChild) this.root.removeChild(this.root.firstChild);
    var node = this.currentNode();
    if (!node) return;
    var card = node.type === "question" ? this.renderQuestion(node) : this.renderResult(node);
    this.root.appendChild(card);
    this.root.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  Wizard.prototype.renderQuestion = function (node) {
    var self = this;
    var step = this.history.length;
    var card = el("div", { className: "wiz-card wiz-question" });

    var header = el("div", { className: "wiz-header" }, [
      el("span", { className: "wiz-step" }, this.s.step + " " + step),
      this.history.length > 1
        ? el("button", { className: "wiz-link", onClick: function () { self.back(); } }, "← " + this.s.back)
        : null,
    ]);
    card.appendChild(header);

    card.appendChild(el("h2", { className: "wiz-q" }, node.text));
    if (node.hint) card.appendChild(el("p", { className: "wiz-hint" }, node.hint));

    var opts = el("div", { className: "wiz-options" });
    node.options.forEach(function (opt) {
      var btn = el("button", {
        className: "wiz-option",
        onClick: function () { self.go(opt.next); },
      });
      btn.appendChild(el("span", { className: "wiz-option-label" }, opt.label));
      if (opt.desc) btn.appendChild(el("span", { className: "wiz-option-desc" }, opt.desc));
      btn.appendChild(el("span", { className: "wiz-arrow", html: "→" }));
      opts.appendChild(btn);
    });
    card.appendChild(opts);

    return card;
  };

  Wizard.prototype.renderResult = function (node) {
    var self = this;
    var card = el("div", { className: "wiz-card wiz-result wiz-level-" + (node.level || "neutral") });

    var header = el("div", { className: "wiz-header" }, [
      el("span", { className: "wiz-step" }, this.s.identity),
      el("button", { className: "wiz-link", onClick: function () { self.start(); } }, "↻ " + this.s.restart),
    ]);
    card.appendChild(header);

    var titleRow = el("div", { className: "wiz-title-row" });
    titleRow.appendChild(el("h2", { className: "wiz-identity" }, node.identity));
    if (node.rank) titleRow.appendChild(el("span", { className: "wiz-rank" }, "#" + node.rank));
    card.appendChild(titleRow);

    if (node.forced) {
      var forced = el("div", { className: "wiz-forced" });
      forced.appendChild(el("span", { className: "wiz-forced-tag" }, this.s.forced));
      forced.appendChild(el("span", { className: "wiz-forced-reason" }, node.forcedReason));
      card.appendChild(forced);
    }

    card.appendChild(el("p", { className: "wiz-summary" }, node.summary));

    if (node.hardening && node.hardening.length) {
      card.appendChild(el("h3", { className: "wiz-section" }, this.s.hardening));
      var ul = el("ul", { className: "wiz-hardening" });
      node.hardening.forEach(function (h) {
        ul.appendChild(el("li", null, h));
      });
      card.appendChild(ul);
      if (node.hardeningRef) {
        card.appendChild(
          el("p", { className: "wiz-link-row" }, [
            el("a", { href: node.hardeningRef, className: "wiz-ref" }, "→ " + this.s.hardeningMore),
          ])
        );
      }
    }

    var actions = el("div", { className: "wiz-actions" });

    if (node.next) {
      actions.appendChild(
        el("button", {
          className: "wiz-primary",
          onClick: function () { self.go(node.next); },
        }, this.s.next + " — " + this.s.privCheckSubtitle + " →")
      );
    }

    if (node.ref) {
      actions.appendChild(el("a", { href: node.ref, className: "wiz-secondary" }, this.s.readMore + " →"));
    }

    actions.appendChild(
      el("button", {
        className: "wiz-secondary",
        onClick: function () { self.back(); },
      }, "← " + this.s.back)
    );

    actions.appendChild(
      el("button", {
        className: "wiz-tertiary",
        onClick: function () { self.start(); },
      }, "↻ " + this.s.restart)
    );

    card.appendChild(actions);
    return card;
  };

  window.Wizard = Wizard;
})();

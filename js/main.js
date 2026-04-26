(function () {
  console.log(5);
  var lightbox = document.getElementById("image-lightbox");
  var navToggle = document.querySelector(".nav-toggle");
  var siteNav = document.querySelector(".site-nav");
  var siteHeader = document.querySelector(".site-header");
  var MOBILE_NAV = window.matchMedia("(max-width: 768px)");
  var openLightboxFn = null;
  var closeLightboxFn = null;

  function isMobileMenuLayout() {
    return MOBILE_NAV.matches;
  }

  function setNavMenuOpen(open) {
    if (!navToggle || !siteNav) return;
    if (open) {
      siteNav.classList.add("is-open");
      navToggle.setAttribute("aria-expanded", "true");
      navToggle.setAttribute("aria-label", "Close menu");
      document.body.classList.add("is-nav-open");
    } else {
      siteNav.classList.remove("is-open");
      navToggle.setAttribute("aria-expanded", "false");
      navToggle.setAttribute("aria-label", "Open menu");
      document.body.classList.remove("is-nav-open");
    }
  }

  if (navToggle && siteNav && siteHeader) {
    if (!navToggle.getAttribute("aria-label")) {
      navToggle.setAttribute("aria-label", "Open menu");
    }

    navToggle.addEventListener("click", function (e) {
      e.stopPropagation();
      setNavMenuOpen(!siteNav.classList.contains("is-open"));
    });

    siteNav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        setNavMenuOpen(false);
      });
    });

    document.addEventListener("click", function (e) {
      if (!isMobileMenuLayout() || !siteNav.classList.contains("is-open")) return;
      if (siteHeader.contains(e.target)) return;
      setNavMenuOpen(false);
    });

    function onViewportNavModeChange() {
      if (!isMobileMenuLayout()) {
        setNavMenuOpen(false);
      }
    }
    if (MOBILE_NAV.addEventListener) {
      MOBILE_NAV.addEventListener("change", onViewportNavModeChange);
    } else if (MOBILE_NAV.addListener) {
      MOBILE_NAV.addListener(onViewportNavModeChange);
    }
  }

  function updateBodyScrollLock() {
    var lbOpen = lightbox && !lightbox.hidden;
    document.body.style.overflow = lbOpen ? "hidden" : "";
  }

  if (lightbox) {
    var backdrop = lightbox.querySelector(".lightbox__backdrop");
    var closeBtn = lightbox.querySelector(".lightbox__close");
    var imgEl = lightbox.querySelector(".lightbox__img");
    var titleEl = lightbox.querySelector(".lightbox__title");
    var lastFocus = null;

    openLightboxFn = function (src, title, altText) {
      lastFocus = document.activeElement;
      imgEl.src = src;
      imgEl.alt = altText || title || "";
      titleEl.textContent = title || "";
      lightbox.hidden = false;
      updateBodyScrollLock();
      if (closeBtn) closeBtn.focus();
    };

    closeLightboxFn = function () {
      lightbox.hidden = true;
      imgEl.removeAttribute("src");
      imgEl.alt = "";
      updateBodyScrollLock();
      if (lastFocus && typeof lastFocus.focus === "function") {
        lastFocus.focus();
      }
    };

    function openLightboxFromTrigger(el) {
      var src = el.getAttribute("data-lightbox-src");
      var title = el.getAttribute("data-lightbox-title") || "";
      var innerImg = el.querySelector("img");
      var altText = innerImg ? innerImg.getAttribute("alt") || "" : "";
      if (src) openLightboxFn(src, title, altText || title);
    }

    document.addEventListener("click", function (e) {
      var t = e.target.closest(
        ".tri-zoom[data-lightbox-src], .gallery-thumb[data-lightbox-src]"
      );
      if (!t) return;
      openLightboxFromTrigger(t);
    });

    document.addEventListener("keydown", function (e) {
      if (e.key !== "Enter" && e.key !== " ") return;
      var tag = (e.target && e.target.tagName) || "";
      if (
        tag === "INPUT" ||
        tag === "TEXTAREA" ||
        tag === "SELECT" ||
        (e.target && e.target.isContentEditable)
      ) {
        return;
      }
      var t = e.target.closest(
        ".tri-zoom[data-lightbox-src], .gallery-thumb[data-lightbox-src]"
      );
      if (!t) return;
      if (e.key === " ") e.preventDefault();
      openLightboxFromTrigger(t);
    });

    if (backdrop) {
      backdrop.addEventListener("click", closeLightboxFn);
    }
    if (closeBtn) {
      closeBtn.addEventListener("click", closeLightboxFn);
    }
  }

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (lightbox && !lightbox.hidden && closeLightboxFn) {
      e.preventDefault();
      closeLightboxFn();
      return;
    }
    if (siteNav && siteNav.classList.contains("is-open") && isMobileMenuLayout()) {
      e.preventDefault();
      setNavMenuOpen(false);
    }
  });

  document.querySelectorAll(".footer-credit").forEach(function (n) { n.remove(); });
})();

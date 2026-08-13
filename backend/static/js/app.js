"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const languageSwitcher = document.getElementById("language-switcher");
  if (languageSwitcher) {
    languageSwitcher.addEventListener("change", () => languageSwitcher.form.submit());
  }
});

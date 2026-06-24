// Navegación del selector de torneo en el formulario de registro:
// al cambiar el torneo, recarga el formulario con sus campos correctos.
document.addEventListener("change", function (e) {
  var el = e.target;
  if (el && el.matches("[data-register-select]")) {
    var url = el.value;
    if (url) window.location.href = url;
  }
});

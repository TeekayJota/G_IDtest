// Navegación del selector de torneo en el formulario de registro:
// al cambiar el torneo, recarga el formulario con sus campos correctos.
document.addEventListener("change", function (e) {
  var el = e.target;
  if (el && el.matches("[data-register-select]")) {
    var url = el.value;
    if (url) window.location.href = url;
  }
});

// Mostrar / ocultar contraseña en cualquier campo con [data-pwd-toggle="id"].
var EYE =
  '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';
var EYE_OFF =
  '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>';

document.addEventListener("click", function (e) {
  var btn = e.target.closest("[data-pwd-toggle]");
  if (!btn) return;
  var input = document.getElementById(btn.getAttribute("data-pwd-toggle"));
  if (!input) return;
  var show = input.type === "password";
  input.type = show ? "text" : "password";
  btn.innerHTML = show ? EYE_OFF : EYE;
  btn.setAttribute("aria-label", show ? "Ocultar contraseña" : "Mostrar contraseña");
});

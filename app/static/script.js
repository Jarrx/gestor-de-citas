document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");

  if (form) {
    const fechaInput = document.getElementById("fecha");

    form.addEventListener("submit", function (e) {
      let valid = true;

      // Validación general de campos requeridos
      const requiredFields = form.querySelectorAll(
        "input[required], select[required]"
      );

      requiredFields.forEach((field) => {
        if (!field.value.trim()) {
          valid = false;
          field.classList.add("is-invalid");
          field.classList.remove("is-valid");
        } else {
          field.classList.remove("is-invalid");
          field.classList.add("is-valid");
        }
      });

      // Validación específica para fecha
      const fechaRegex = /^\d{2}\/\d{2}\/\d{4}$/;
      if (!fechaRegex.test(fechaInput.value)) {
        valid = false;
        fechaInput.classList.add("is-invalid");
        fechaInput.classList.remove("is-valid");
      } else {
        fechaInput.classList.remove("is-invalid");
        fechaInput.classList.add("is-valid");
      }

      form.classList.add("was-validated");

      if (!valid) {
        e.preventDefault(); // Evita el envío
        alert("Por favor completa todos los campos requeridos correctamente.");
      }
    });
  }

  const eliminarButtons = document.querySelectorAll(".btn-eliminar");
  const modal = document.getElementById("confirmarEliminarModal");
  const formEliminar = document.getElementById("formEliminar");
  const mensaje = document.getElementById("mensajeConfirmacion");

  if (eliminarButtons.length && modal && formEliminar && mensaje) {
    const bootstrapModal = new bootstrap.Modal(modal);

    eliminarButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const citaId = button.getAttribute("data-id");
        const nombre = button.getAttribute("data-nombre");

        // Actualizar acción y texto
        formEliminar.action = `/eliminar/${citaId}`;
        mensaje.textContent = `¿Estás seguro de que deseas eliminar la cita de ${nombre}?`;

        bootstrapModal.show();
      });
    });
  }
});

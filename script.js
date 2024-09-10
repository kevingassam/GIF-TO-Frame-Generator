$(document).ready(function () {
  $(".form-upload-div").click(function () {
    $("#input-file").click();
    // if image selected change source preview
    $("#input-file").change(function () {
      var file = this.files[0];
      var reader = new FileReader();
      reader.onload = function (event) {
        $("#preview-image").attr("src", event.target.result);
      };
      reader.readAsDataURL(file);
    });
  });

  $("#form").submit(function (e) {
    e.preventDefault();
    $("#error").text("");

    var form = $(this);
    var actionUrl = form.attr("action");

    // Créer une nouvelle instance de FormData pour gérer les fichiers
    var formData = new FormData(form[0]);

    $.ajax({
      type: "POST",
      url: actionUrl,
      data: formData,
      processData: false,
      contentType: false,
      dataType: "json",
      success: function (data) {
        // Traiter la réponse
        if (data.success) {
          $.toast({
            heading: "Félicitation !",
            text: "Votre code a été générer",
            position: "bottom-right",
            icon: "success",
            stack: false,
          });
          // reset form
          form[0].reset();
          $("#preview-image").attr(
            "src",
            "https://img.icons8.com/ios/20/1A1A1A/code--v1.png"
          );
          var a = document.createElement("a");
          a.href = data.download_link_zip;
          a.download = "CODE";
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        } else {
          $.toast({
            heading: "Erreur !",
            text: data.message,
            position: "bottom-right",
            icon: "error",
            stack: false,
          });
        }
      },
      error: function (xhr, status, error) {
        // Gestion des erreurs dans l'appel Ajax
        console.log(xhr.responseText);
        // Afficher un message d'erreur
      },
    });
  });
});

//preloader
$(window).on("load", function () {
  setTimeout(function () {
    $(".preloader").fadeOut("slow", function () {
      $(".content").fadeIn("slow");
    });
  }, 2000); // 2000 millisecondes = 2 secondes
});

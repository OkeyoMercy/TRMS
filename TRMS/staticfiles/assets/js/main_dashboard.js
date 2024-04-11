document.addEventListener("DOMContentLoaded", function() {
    var showProfileComponentFlag = document.getElementById("showProfileComponentFlag");
    if (showProfileComponentFlag && showProfileComponentFlag.value === "true") {
      document.getElementById("profileComponentContainer").style.display = "block";
    }
  });
  
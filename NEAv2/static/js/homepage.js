//defining elements by class
const popup = document.querySelector(".popup");
const popupr = document.querySelector(".popupr");
const loginbtn = document.querySelector(".loginbutton");
const registerbtn = document.querySelector(".registerbutton");

//checks if a mouse click occurs in which a popup box should appear and the other pop up box is removed
loginbtn.addEventListener("click", () => {
  popup.classList.add("active-popup");
  popupr.classList.remove("active-popupr");
});

//checks if a mouse click occurs in which a popup box should appear and the other pop up box is removed
registerbtn.addEventListener("click", () => {
  popupr.classList.add("active-popupr");
  popup.classList.remove("active-popup");
});

document
  .getElementById("registerform")
  .addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent the form from submitting

    // Get the values of the password fields
    const password = document.getElementById("password").value;
    const confirmpassword = document.getElementById("confirmpassword").value;

    // Check if passwords match
    if (password.length < 7) {
      console.log("Password too short");
      document.getElementById("error1").style.display = "block";
      document.getElementById("error").style.display = "none";
    } else if (password === confirmpassword) {
      // Passwords match
      console.log("Passwords match!");
      // You can proceed with form submission or any other action here
      document.getElementById("registerform").submit();
    } else {
      // Passwords do not match
      console.log("Passwords do not match!");
      // You can display an error message or take appropriate action here
      document.getElementById("error").style.display = "block";
      document.getElementById("error1").style.display = "none";
      // Optionally, you can also clear the password fields for the user to try again
      document.getElementById("password").value = "";
      document.getElementById("confirmpassword").value = "";
    }
  });

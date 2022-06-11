const profile = document.querySelector(".profile");
const login = document.querySelector(".login");

login.addEventListener("click", () => {
  profile.classList.toggle("show-profile");
});

const profile = document.querySelector(".profile");
const login = document.querySelector(".login");

login.addEventListener("click", () => {
  profile.classList.toggle("show-profile");
});

const btn = document.querySelector(".btn");

btn.addEventListener("click", () => {
  btn.classList.toggle("btn--loading");
});

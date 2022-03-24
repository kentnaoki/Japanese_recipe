const menu = document.getElementById("menu");
const bar = document.getElementById("bar-dynamic");
const back = document.getElementById("back");
const nav = document.getElementById("nav");
  
bar.addEventListener("click", () => {
    if (nav.className === "navi") {
        nav.classList.add("open-menu");
        back.classList.add("open");
        menu.textContent = "CLOSE";
    }else {nav.classList.remove("open-menu");
        back.classList.remove("open");
        menu.textContent = "CLOSE";
        }
});

menu.addEventListener("click", () => {
  if (nav.className === "navi") {
      nav.classList.add("open-menu");
      back.classList.add("open");
      menu.textContent = "CLOSE";
  }else {nav.classList.remove("open-menu");
      back.classList.remove("open");
        menu.textContent = "Menu";
        }
});
  
back.addEventListener("click", () => {
    back.classList.remove("open");
    nav.classList.remove("open-menu");
    menu.textContent = "Menu";
});


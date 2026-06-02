const form = document.getElementById("contactForm");
const formMessage = document.getElementById("formMessage");

if (form) {
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const name = form.name.value.trim();
    const message = form.message.value.trim();

    if (!name || !message) {
      formMessage.textContent = "모든 항목을 입력해주세요.";
      return;
    }

    formMessage.textContent = `감사합니다, ${name}! 메시지가 전송되었습니다.`;
    form.reset();
  });
}

window.addEventListener("scroll", () => {
  const header = document.querySelector(".topbar");
  if (!header) return;
  if (window.scrollY > 20) {
    header.style.background = "rgba(10, 14, 22, 0.98)";
    header.style.borderBottom = "1px solid rgba(148, 163, 184, 0.14)";
  } else {
    header.style.background = "rgba(14, 18, 28, 0.84)";
    header.style.borderBottom = "1px solid rgba(148, 163, 184, 0.12)";
  }
});

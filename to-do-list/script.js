const todoForm = document.getElementById("todo-form");
const todoInput = document.getElementById("todo-input");
const importantToggle = document.getElementById("important-toggle");
const todoListEl = document.getElementById("todo-list");
const todayDateEl = document.getElementById("today-date");
const taskCountEl = document.getElementById("task-count");
const completedCountEl = document.getElementById("completed-count");
const activeCountEl = document.getElementById("active-count");
const completionRateEl = document.getElementById("completion-rate");
const progressBarEl = document.getElementById("progress-bar");
const clearCompletedButton = document.getElementById("clear-completed-btn");
const clearAllButton = document.getElementById("clear-all-btn");
const filterButtons = document.querySelectorAll("[data-filter]");

const STORAGE_KEY = "todo-list-today";
let currentFilter = "all";

function getTodayKey() {
  const now = new Date();
  return now.toISOString().slice(0, 10);
}

function formatDate(date) {
  return date.toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
    weekday: "short",
  });
}

function loadTasks() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return [];
  }
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    console.error("할 일 불러오기 실패:", error);
    return [];
  }
}

function saveTasks(tasks) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
}

function getFilteredTasks(tasks) {
  return tasks.filter((task) => {
    if (currentFilter === "active") {
      return !task.done;
    }
    if (currentFilter === "completed") {
      return task.done;
    }
    return true;
  });
}

function sortTasks(tasks) {
  return [...tasks].sort((a, b) => {
    if (a.important !== b.important) {
      return b.important - a.important;
    }
    return a.createdAt - b.createdAt;
  });
}

function setActiveFilter(filter) {
  currentFilter = filter;
  filterButtons.forEach((button) => {
    if (button.dataset.filter === filter) {
      button.classList.add("bg-slate-900", "text-white", "border-slate-900");
      button.classList.remove("bg-slate-100", "text-slate-700");
    } else {
      button.classList.remove("bg-slate-900", "text-white", "border-slate-900");
      button.classList.add("bg-slate-100", "text-slate-700");
    }
  });
  renderTasks();
}

function getTodayTasks() {
  const todayKey = getTodayKey();
  return loadTasks().filter((task) => task.date === todayKey);
}

function updateStats(tasks) {
  const total = tasks.length;
  const completed = tasks.filter((task) => task.done).length;
  const active = total - completed;
  const rate = total === 0 ? 0 : Math.round((completed / total) * 100);

  taskCountEl.textContent = `${total}개`;
  completedCountEl.textContent = `완료 ${completed}개`;
  activeCountEl.textContent = `진행중 ${active}개`;
  completionRateEl.textContent = `${rate}%`;
  progressBarEl.style.width = `${rate}%`;
}

function renderTasks() {
  const todayTasks = getTodayTasks();
  const visibleTasks = sortTasks(getFilteredTasks(todayTasks));
  todoListEl.innerHTML = "";

  updateStats(todayTasks);

  if (visibleTasks.length === 0) {
    const emptyItem = document.createElement("li");
    emptyItem.className = "todo-item justify-center text-slate-500";
    emptyItem.textContent = currentFilter === "all" ? "오늘의 할 일이 없습니다. 새 할 일을 추가해보세요." : "선택한 보기에는 항목이 없습니다.";
    todoListEl.appendChild(emptyItem);
    return;
  }

  visibleTasks.forEach((task) => {
    const item = document.createElement("li");
    item.className = "todo-item";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = task.done;
    checkbox.addEventListener("change", () => toggleTask(task.id));

    const content = document.createElement("div");
    content.className = "min-w-0";

    const label = document.createElement("p");
    label.className = "todo-label" + (task.done ? " completed" : "");
    label.textContent = task.text;

    content.appendChild(label);

    if (task.important) {
      const badge = document.createElement("span");
      badge.className = "mt-2 inline-flex rounded-full bg-fuchsia-100 px-2.5 py-1 text-xs font-semibold text-fuchsia-700";
      badge.textContent = "중요";
      content.appendChild(badge);
    }

    const deleteButton = document.createElement("button");
    deleteButton.className = "todo-delete";
    deleteButton.type = "button";
    deleteButton.textContent = "삭제";
    deleteButton.addEventListener("click", () => removeTask(task.id));

    item.appendChild(checkbox);
    item.appendChild(content);
    item.appendChild(deleteButton);

    todoListEl.appendChild(item);
  });
}

function addTask(text) {
  const trimmed = text.trim();
  if (!trimmed) {
    return;
  }

  const tasks = loadTasks();
  const newTask = {
    id: Date.now().toString(),
    text: trimmed,
    done: false,
    important: importantToggle.checked,
    date: getTodayKey(),
    createdAt: Date.now(),
  };
  tasks.push(newTask);
  saveTasks(tasks);
  renderTasks();
}

function clearCompletedTasks() {
  const tasks = loadTasks();
  const updated = tasks.filter((task) => !task.done);
  saveTasks(updated);
  renderTasks();
}

function clearAllTasks() {
  if (!confirm("전체 할 일을 삭제하시겠습니까?")) {
    return;
  }
  saveTasks([]);
  renderTasks();
}

function toggleTask(id) {
  const tasks = loadTasks();
  const updated = tasks.map((task) => {
    if (task.id === id) {
      return { ...task, done: !task.done };
    }
    return task;
  });
  saveTasks(updated);
  renderTasks();
}

function removeTask(id) {
  const tasks = loadTasks();
  const updated = tasks.filter((task) => task.id !== id);
  saveTasks(updated);
  renderTasks();
}

function initialize() {
  todayDateEl.textContent = formatDate(new Date());
  setActiveFilter(currentFilter);
}

todoForm.addEventListener("submit", (event) => {
  event.preventDefault();
  addTask(todoInput.value);
  todoInput.value = "";
  importantToggle.checked = false;
  todoInput.focus();
});

clearCompletedButton.addEventListener("click", clearCompletedTasks);
clearAllButton.addEventListener("click", clearAllTasks);
filterButtons.forEach((button) => {
  button.addEventListener("click", () => setActiveFilter(button.dataset.filter));
});

window.addEventListener("DOMContentLoaded", initialize);

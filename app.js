const $ = (selector) => document.querySelector(selector);
const form = $("#documentForm");
const state = { language: "English", draftTitle: "Agreement" };
const sections = { empty: $("#emptyState"), loading: $("#loadingState"), error: $("#errorState"), editor: $("#editorState") };

function showState(name) {
  Object.entries(sections).forEach(([key, element]) => element.classList.toggle("hidden", key !== name));
}
function toast(message) {
  const node = $("#toast"); node.textContent = message; node.classList.add("show");
  clearTimeout(toast.timer); toast.timer = setTimeout(() => node.classList.remove("show"), 2600);
}
function setStatus(text, mode = "ready") {
  const badge = $("#statusBadge"); badge.className = `status-badge ${mode}`; badge.innerHTML = `<i></i> ${text}`;
}
function addRecent(title) {
  const list = $("#recentList");
  if (list.querySelector(".empty-recent")) list.innerHTML = "";
  const item = document.createElement("div"); item.className = "recent-entry"; item.textContent = title;
  item.title = title; list.prepend(item);
  while (list.children.length > 5) list.lastElementChild.remove();
}

$("#terms").addEventListener("input", (event) => { $("#charCount").textContent = `${event.target.value.length} / 5000`; });
document.querySelectorAll(".language-option").forEach((button) => button.addEventListener("click", () => {
  document.querySelectorAll(".language-option").forEach((item) => item.classList.remove("selected"));
  button.classList.add("selected"); state.language = button.dataset.language;
}));

async function createDraft(event) {
  event?.preventDefault();
  if (!form.reportValidity()) return;
  const button = $("#generateButton"); button.disabled = true; showState("loading"); setStatus("DRAFTING", "working");
  const request = {
    document_type: $("#documentType").value,
    first_party: $("#firstParty").value.trim(),
    second_party: $("#secondParty").value.trim(),
    effective_date: $("#effectiveDate").value,
    jurisdiction: $("#jurisdiction").value,
    terms: $("#terms").value.trim(),
    language: state.language,
  };
  try {
    const response = await fetch("/api/generate", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(request) });
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || "Please check your details and try again.");
    state.draftTitle = request.document_type;
    $("#draftTitle").textContent = request.document_type;
    $("#draftContent").value = result.content;
    $("#draftMode").textContent = result.demo_mode ? "· DEMO DRAFT" : "· AI DRAFT";
    showState("editor"); setStatus("DRAFT READY", "done"); addRecent(request.document_type);
  } catch (error) {
    $("#errorMessage").textContent = error.message || "A connection error occurred.";
    showState("error"); setStatus("NEEDS ATTENTION", "ready");
  } finally { button.disabled = false; }
}
form.addEventListener("submit", createDraft);
$("#retryButton").addEventListener("click", createDraft);
$("#resetButton").addEventListener("click", () => { showState("empty"); setStatus("READY WHEN YOU ARE", "ready"); });
$("#newDraftNav").addEventListener("click", () => { form.reset(); $("#charCount").textContent = "0 / 5000"; state.language = "English"; document.querySelectorAll(".language-option").forEach((item) => item.classList.toggle("selected", item.dataset.language === "English")); showState("empty"); setStatus("READY WHEN YOU ARE", "ready"); window.scrollTo({ top: 0, behavior: "smooth" }); });
$("#templatesNav").addEventListener("click", () => toast("Choose a document type to start with a ready-made template."));
$("#helpButton").addEventListener("click", () => $("#aboutDialog").showModal());
$("#footerAbout").addEventListener("click", () => $("#aboutDialog").showModal());
$("#closeDialog").addEventListener("click", () => $("#aboutDialog").close());
$("#copyButton").addEventListener("click", async () => {
  try { await navigator.clipboard.writeText($("#draftContent").value); toast("Draft copied to clipboard."); }
  catch { $("#draftContent").select(); document.execCommand("copy"); toast("Draft copied to clipboard."); }
});
document.querySelectorAll(".export-button").forEach((button) => button.addEventListener("click", async () => {
  const original = button.innerHTML; button.disabled = true; button.innerHTML = "Preparing…";
  try {
    const response = await fetch(`/api/export/${button.dataset.format}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title: state.draftTitle, content: $("#draftContent").value }) });
    if (!response.ok) { const error = await response.json(); throw new Error(error.detail || "Download failed."); }
    const blob = await response.blob(); const url = URL.createObjectURL(blob); const link = document.createElement("a");
    link.href = url; link.download = `legalease-${button.dataset.format === "txt" ? "draft.txt" : `draft.${button.dataset.format}`}`;
    document.body.appendChild(link); link.click(); link.remove(); URL.revokeObjectURL(url); toast(`${button.dataset.format.toUpperCase()} downloaded.`);
  } catch (error) { toast(error.message); }
  finally { button.disabled = false; button.innerHTML = original; }
}));

const dateInput = $("#effectiveDate");
dateInput.value = new Date().toISOString().slice(0, 10);
document.addEventListener("keydown", (event) => { if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "n") { event.preventDefault(); $("#newDraftNav").click(); } });

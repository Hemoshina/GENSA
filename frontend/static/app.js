async function askAI() {
  const query = document.getElementById("query").value.trim();
  if (!query) {
    alert("Please enter a query!");
    return;
  }

  try {
    const response = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });

    const data = await response.json();
    document.getElementById("response").innerText = data.final_answer || "No response";
  } catch (err) {
    console.error("Error calling API:", err);
    document.getElementById("response").innerText = "Network error occured";
  }
}
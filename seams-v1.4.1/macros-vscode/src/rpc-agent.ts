export async function runAgentTool(toolName: string, payload: any): Promise<{code: string; notes: string}> {
  const url = `http://127.0.0.1:8765/tool/${encodeURIComponent(toolName)}`;
  const res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ payload }) });
  if (!res.ok) throw new Error(`Agent server error ${res.status}: ${await res.text()}`);
  return await res.json();
}

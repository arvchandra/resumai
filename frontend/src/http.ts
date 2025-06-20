export async function fetchJobDescriptionText() {
  const response = await fetch("http://127.0.0.1:8000/tailor/api/jobposting/?linkedInJobID=4455567");
  const jsonData = await response.json();

  if (!response.ok) {
    throw new Error("Failed to fetch job posting text");
  }

  return jsonData;
}
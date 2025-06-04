export async function fetchJobPostingText() {
  const response = await fetch("http://127.0.0.1:8000/jobposting");
  const resData = await response.json();

  if (!response.ok) {
    throw new Error("Failed to fetch job posting text");
  }

  return resData;
}
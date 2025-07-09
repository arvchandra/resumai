export async function fetchJobDescriptionText() {
  const response = await fetch("http://127.0.0.1:8000/tailor/jobposting/?linkedInJobID=4455567");
  const jsonData = await response.json();

  if (!response.ok) {
    throw new Error("Failed to fetch job posting text");
  }

  return jsonData;
}

export async function fetchUserResumes() {
  const response = await fetch("http://127.0.0.1:8000/tailor/users/2/resumes/");
  const jsonData = await response.json();

  if (!response.ok) {
    throw new Error("Failed to fetch user-uploaded resumes.");
  }

  return jsonData;
}

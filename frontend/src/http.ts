export async function fetchUserResumes() {
  const response = await fetch("http://localhost:8000/tailor/users/2/resumes/");
  const jsonData = await response.json();

  if (!response.ok) {
    throw new Error("Failed to fetch user-uploaded resumes.");
  }

  return jsonData;
}

export async function fetchTailoredResumes() {
  const response = await fetch("http://localhost:8000/tailor/users/2/tailored-resumes/");
  const jsonData = await response.json();

  if (!response.ok) {
    throw new Error("Failed to fetch tailored resumes");
  }

  return jsonData;
}

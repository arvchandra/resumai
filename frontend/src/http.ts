export async function fetchUserResumes() {
  const response = await fetch("http://127.0.0.1:8000/tailor/users/2/resumes/");
  const jsonData = await response.json();

  if (!response.ok) {
    throw new Error("Failed to fetch user-uploaded resumes.");
  }

  return jsonData;
}

export async function fetchTailoredResumes() {
    const response  = await fetch("https://127.0.0.1:8000/tailor/users/2/resumes/tailored");
    const jsonData = await response.json();

    if (!response.ok) {
        throw new Error("Failed to fetch tailored resumes");
    }

    return jsonData;
}

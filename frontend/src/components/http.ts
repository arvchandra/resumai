import { usersApiUrl } from './settings';

async function fetchUsers() {
  const response = await fetch(usersApiUrl);
  const jsonData = await response.json();

  if (!response.ok) {
    throw new Error('Unable to retrieve users.');
  }

  return jsonData;
}

export default fetchUsers;
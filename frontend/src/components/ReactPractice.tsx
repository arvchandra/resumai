/* INSTRUCTIONS:

Fetch data from this public API:
https://jsonplaceholder.typicode.com/users

Displays the user data in a card grid with subtle animations

Use useEffect + fetch or axios

Type the API response using an interface

Show loading and error states

Display at least: name, email, company.name, address.city

Add at least one interactive feature (e.g. details modal)
*/
import { useEffect } from 'react';

import UsersGrid from './UsersGrid';

import fetchUsers from './http';
import useFetch from '../components/hooks/useFetch';
import { useUsersContext } from './contexts/UsersContext';

const ReactPractice = () => {
  // Fetch data from API (async)
  // Show loading state
  // Store results in state
  // Display the results in a grid of cards
  // Show a modal with more details if card is clicked
  const { fetchedData, isFetching, error } = useFetch(fetchUsers);
  const { setUsers } = useUsersContext();

  useEffect(() => {
    if (fetchedData) {
      setUsers(fetchedData);
    }
  }, [setUsers, fetchedData]);

  return (
    <div>
      {isFetching ? <span>Loading...</span> : 
        error ? <span>Error: {error}</span> :
        <UsersGrid /> 
      }
    </div>
  )
}

export default ReactPractice;
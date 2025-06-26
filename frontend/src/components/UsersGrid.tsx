// name, email, company.name, address.city
/*
{
    "id": 1,
    "name": "Leanne Graham",
    "username": "Bret",
    "email": "Sincere@april.biz",
    "address": {
      "street": "Kulas Light",
      "suite": "Apt. 556",
      "city": "Gwenborough",
      "zipcode": "92998-3874",
      "geo": {
        "lat": "-37.3159",
        "lng": "81.1496"
      }
    },
    "phone": "1-770-736-8031 x56442",
    "website": "hildegard.org",
    "company": {
      "name": "Romaguera-Crona",
      "catchPhrase": "Multi-layered client-server neural-net",
      "bs": "harness real-time e-markets"
    }
  },
*/
import UserCard from './UserCard';

import './styles/UserGrid.css';

import { useUsersContext } from './contexts/UsersContext';

const UsersGrid = () => {
  const { users } = useUsersContext();

  if (users.length === 0) {
    return <span>No users to display.</span>
  }

  return (
    <div className="usersGrid"> 
      {users.map((user) => {
        return <UserCard key={user.id} user={user} />;
      })}
    </div>
  );
}

export default UsersGrid;
import './styles/UserCard.css';

import type { User } from './interfaces/User';

interface UserCardProps {
  user: User;
}

const UserCard: React.FC<UserCardProps> = ({ user }) => {
  return (
    <div className="userCard">
      <div className="userName">{user.name}</div>
      <div className="userEmail">{user.email}</div>
      <div className="userCompany">{user.company.name}</div>
      <div className="userCity">{user.address.city}</div>
    </div>
  )
}

export default UserCard;
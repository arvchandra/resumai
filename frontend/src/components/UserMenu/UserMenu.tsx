import { useAuth } from "../../contexts/AuthContext"

export default function UserMenu() {
  const { userInfo } = useAuth();

  if (!userInfo) {
    return null;
  }

  return (
    <div>
      Welcome, {userInfo?.firstName}
    </div>
  )
}

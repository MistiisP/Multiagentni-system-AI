import React from 'react';
import '../../css/User.css';
import { useAuth } from '../../services/authContext';

interface UserAvatarProps {
  size?: 'medium' | 'large';
  src?: string;
  alt?: string;
  color?: 'primary';
  className?: string;
}

const UserAvatar: React.FC<UserAvatarProps> = ({ size = 'medium', src, alt, color = 'primary', className = '' }) => {
  const { user, loading, error } = useAuth();

  const getInitials = (name: string): string => {
    if (!name) return '?';
    const nameParts = name.trim().split(' ');
    return nameParts.length >= 2 ? `${nameParts[0][0]}${nameParts[1][0]}`.toUpperCase() : name.charAt(0).toUpperCase();
  };

  if (error) {
    return <div className={`user-avatar ${size} error-avatar`}>!</div>;
  }

  const initials = user ? getInitials(user.name) : '?';

  return (
    <div className={`user-avatar ${size} ${color} ${className}`}>
      {loading ? (
        <span className="avatar-loading">...</span>
      ) : src ? (
        <img src={src} alt={alt || user?.name || 'User'} className="avatar-image" />
      ) : (
        <span className="avatar-text">{initials}</span>
      )}
    </div>
  );
};

export default UserAvatar;
import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, Button, Input, Label } from '@/components/ui';
import { useToast } from '@/hooks/use-toast';
import { User as UserIcon, Mail, Lock, LogOut } from 'lucide-react'; // Added LogOut icon
import { useAuth } from '@/hooks/use-auth'; // Import useAuth hook
import { useLocation } from 'wouter'; // Import useLocation hook

// Mock API call for fetching user data
const fetchUserData = async () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        username: 'vareon_user',
        email: 'user@vareon.com',
        // In a real app, password would not be sent
      });
    }, 500);
  });
};

// Mock API call for updating user data
const updateUserData = async (data: { username?: string; email?: string; password?: string }) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (data.username === 'admin') { // Simulate a validation error
        reject(new Error('Username "admin" is reserved.'));
      } else {
        resolve({ message: 'Profile updated successfully!' });
      }
    }, 1000);
  });
};

export default function UserProfile() {
  const { toast } = useToast();
  const { logout } = useAuth(); // Get logout function from useAuth
  const [, setLocation] = useLocation(); // Get setLocation for redirection
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetchUserData().then((data: any) => {
      setUsername(data.username);
      setEmail(data.email);
      setLoading(false);
    }).catch(error => {
      toast({
        title: 'Error',
        description: `Failed to load user data: ${error.message}`,
        variant: 'destructive',
      });
      setLoading(false);
    });
  }, [toast]);

  const handleProfileUpdate = async () => {
    setLoading(true);
    try {
      const updatePayload: { username?: string; email?: string } = {};
      if (username) updatePayload.username = username;
      if (email) updatePayload.email = email;

      await updateUserData(updatePayload);
      toast({
        title: 'Profile Updated',
        description: 'Your profile information has been updated.',
      });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: `Failed to update profile: ${error.message}`,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async () => {
    setLoading(true);
    if (newPassword !== confirmNewPassword) {
      toast({
        title: 'Error',
        description: 'New password and confirmation do not match.',
        variant: 'destructive',
      });
      setLoading(false);
      return;
    }
    if (!currentPassword || !newPassword) {
      toast({
        title: 'Error',
        description: 'Current and new passwords cannot be empty.',
        variant: 'destructive',
      });
      setLoading(false);
      return;
    }

    try {
      await updateUserData({ password: newPassword }); // In real app, send currentPassword for verification
      toast({
        title: 'Password Updated',
        description: 'Your password has been changed successfully.',
      });
      setCurrentPassword('');
      setNewPassword('');
      setConfirmNewPassword('');
    } catch (error: any) {
      toast({
        title: 'Error',
        description: `Failed to change password: ${error.message}`,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    setLocation('/auth'); // Redirect to auth page after logout
    toast({
      title: 'Logged Out',
      description: 'You have been successfully logged out.',
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full">
        <p className="text-muted-foreground">Loading user profile...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <UserIcon className="h-5 w-5 text-primary" />
            User Profile
          </CardTitle>
          <CardDescription>Manage your account settings and profile information.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="username">Username</Label>
            <Input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
            />
          </div>
          <Button onClick={handleProfileUpdate} disabled={loading}>
            {loading ? 'Saving...' : 'Save Profile'}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lock className="h-5 w-5 text-primary" />
            Change Password
          </CardTitle>
          <CardDescription>Update your account password.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="current-password">Current Password</Label>
            <Input
              id="current-password"
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              disabled={loading}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="new-password">New Password</Label>
            <Input
              id="new-password"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              disabled={loading}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="confirm-new-password">Confirm New Password</Label>
            <Input
              id="confirm-new-password"
              type="password"
              value={confirmNewPassword}
              onChange={(e) => setConfirmNewPassword(e.target.value)}
              disabled={loading}
            />
          </div>
          <Button onClick={handleChangePassword} disabled={loading}>
            {loading ? 'Changing...' : 'Change Password'}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <LogOut className="h-5 w-5 text-primary" />
            Account Actions
          </CardTitle>
          <CardDescription>Perform actions related to your account.</CardDescription>
        </CardHeader>
        <CardContent>
          <Button variant="destructive" onClick={handleLogout} disabled={loading}>
            <LogOut className="h-4 w-4 mr-2" />
            Logout
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

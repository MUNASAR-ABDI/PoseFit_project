"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { User } from "lucide-react";

type UserProfile = {
  email: string;
  first_name: string;
  last_name: string;
  age?: number | null;
  gender?: string | null;
  weight?: number | null;
  height?: number | null;
  body_metrics?: {
    bmi?: number;
    bmi_category?: string;
  };
};

export function UserProfileCard() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchProfile() {
      try {
        const response = await fetch("/api/profile", {
          credentials: "include",
        });
        
        if (response.ok) {
          const data = await response.json();
          setProfile(data);
        }
      } catch (error) {
        console.error("Error fetching profile:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchProfile();
  }, []);

  if (loading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium">Profile</CardTitle>
          <User className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="h-4 w-24 animate-pulse bg-muted mb-2 rounded"></div>
          <div className="h-4 w-32 animate-pulse bg-muted mb-2 rounded"></div>
          <div className="h-4 w-20 animate-pulse bg-muted rounded"></div>
        </CardContent>
      </Card>
    );
  }

  if (!profile) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium">Profile</CardTitle>
          <User className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Profile not available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium">Your Profile</CardTitle>
        <User className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="text-base font-medium">{profile.first_name} {profile.last_name}</div>
        <div className="text-sm text-muted-foreground">{profile.email}</div>
        
        {/* Only show profile details that were provided during signup */}
        <div className="pt-2 space-y-1">
          {profile.age && (
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Age:</span>
              <span>{profile.age}</span>
            </div>
          )}
          
          {profile.gender && (
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Gender:</span>
              <span>{profile.gender}</span>
            </div>
          )}
          
          {profile.height && (
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Height:</span>
              <span>{profile.height} cm</span>
            </div>
          )}
          
          {profile.weight && (
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Weight:</span>
              <span>{profile.weight} kg</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
} 
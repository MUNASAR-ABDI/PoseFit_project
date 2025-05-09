'use client';

import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { BarChart3, Calendar, User } from "lucide-react";

export function QuickLinks() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Links</CardTitle>
        <CardDescription>Frequently used pages</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <Button variant="outline" className="w-full justify-start" asChild>
            <Link href="/profile">
              <User className="mr-2 h-4 w-4" /> Profile Settings
            </Link>
          </Button>
          <Button variant="outline" className="w-full justify-start" asChild>
            <Link href="/workouts/history">
              <Calendar className="mr-2 h-4 w-4" /> Workout History
            </Link>
          </Button>
          <Button variant="outline" className="w-full justify-start" asChild>
            <Link href="/progress">
              <BarChart3 className="mr-2 h-4 w-4" /> Progress Charts
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
} 
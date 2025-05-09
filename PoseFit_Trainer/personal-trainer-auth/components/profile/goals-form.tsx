"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { toast } from "@/hooks/use-toast"

const goalsFormSchema = z.object({
  primaryGoal: z.string({
    required_error: "Please select a primary goal.",
  }),
  workoutFrequency: z.string({
    required_error: "Please select your workout frequency.",
  }),
  workoutDuration: z.number({
    required_error: "Please select your preferred workout duration.",
  }),
  fitnessLevel: z.string({
    required_error: "Please select your fitness level.",
  }),
})

type GoalsFormValues = z.infer<typeof goalsFormSchema>

export function GoalsForm() {
  const [loading, setLoading] = useState(true);
  
  const form = useForm<GoalsFormValues>({
    resolver: zodResolver(goalsFormSchema),
    defaultValues: {
      primaryGoal: "general",
      workoutFrequency: "3-4",
      workoutDuration: 45, 
      fitnessLevel: "beginner",
    },
  });

  useEffect(() => {
    async function fetchProfile() {
      try {
        setLoading(true);
        const response = await fetch("/api/profile", {
          credentials: "include",
        });
        
        if (response.ok) {
          const data = await response.json();
          
          // Get goals from the profile if they exist
          const goals = data.goals || {};
          
          // Map the fitness goal type to our form values
          let primaryGoal = "general";
          if (goals.fitness_goal_type) {
            // Map from backend values to form values
            const goalMap: Record<string, string> = {
              "weight_loss": "weight-loss",
              "muscle_gain": "muscle-gain",
              "strength_building": "strength",
              "endurance": "endurance",
              "general_fitness": "general"
            };
            primaryGoal = goalMap[goals.fitness_goal_type] || "general";
          }
          
          // Map weekly workouts to frequency ranges
          let workoutFrequency = "3-4";
          if (goals.weekly_workouts) {
            const weekly = goals.weekly_workouts;
            if (weekly <= 2) workoutFrequency = "1-2";
            else if (weekly <= 4) workoutFrequency = "3-4";
            else if (weekly <= 6) workoutFrequency = "5-6";
            else workoutFrequency = "7+";
          }
          
          // Reset form with user data
          form.reset({
            primaryGoal,
            workoutFrequency,
            workoutDuration: goals.minutes_per_workout || 45,
            fitnessLevel: data.body_metrics?.fitness_level || "beginner",
          });
        }
      } catch (error) {
        console.error("Error fetching profile:", error);
        toast({
          title: "Error",
          description: "Failed to load profile data.",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    }

    fetchProfile();
  }, [form]);

  async function onSubmit(data: GoalsFormValues) {
    try {
      // In a real implementation, you would send this data to your API
      toast({
        title: "Goals updated",
        description: "Your fitness goals have been updated successfully.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update goals.",
        variant: "destructive",
      });
    }
  }

  if (loading) {
    return <div className="space-y-4">
      <div className="h-4 w-24 animate-pulse bg-muted rounded"></div>
      <div className="h-10 w-full animate-pulse bg-muted rounded"></div>
      <div className="h-4 w-24 animate-pulse bg-muted rounded"></div>
      <div className="h-10 w-full animate-pulse bg-muted rounded"></div>
    </div>;
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <FormField
          control={form.control}
          name="primaryGoal"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Primary Goal</FormLabel>
              <FormControl>
                <RadioGroup
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                  className="flex flex-col space-y-1"
                >
                  <FormItem className="flex items-center space-x-3 space-y-0">
                    <FormControl>
                      <RadioGroupItem value="weight-loss" />
                    </FormControl>
                    <FormLabel className="font-normal">Weight Loss</FormLabel>
                  </FormItem>
                  <FormItem className="flex items-center space-x-3 space-y-0">
                    <FormControl>
                      <RadioGroupItem value="muscle-gain" />
                    </FormControl>
                    <FormLabel className="font-normal">Muscle Gain</FormLabel>
                  </FormItem>
                  <FormItem className="flex items-center space-x-3 space-y-0">
                    <FormControl>
                      <RadioGroupItem value="strength" />
                    </FormControl>
                    <FormLabel className="font-normal">Strength Building</FormLabel>
                  </FormItem>
                  <FormItem className="flex items-center space-x-3 space-y-0">
                    <FormControl>
                      <RadioGroupItem value="endurance" />
                    </FormControl>
                    <FormLabel className="font-normal">Endurance</FormLabel>
                  </FormItem>
                  <FormItem className="flex items-center space-x-3 space-y-0">
                    <FormControl>
                      <RadioGroupItem value="general" />
                    </FormControl>
                    <FormLabel className="font-normal">General Fitness</FormLabel>
                  </FormItem>
                </RadioGroup>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="workoutFrequency"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Workout Frequency</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select workout frequency" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="1-2">1-2 times per week</SelectItem>
                  <SelectItem value="3-4">3-4 times per week</SelectItem>
                  <SelectItem value="5-6">5-6 times per week</SelectItem>
                  <SelectItem value="7+">Daily</SelectItem>
                </SelectContent>
              </Select>
              <FormDescription>How often you plan to work out each week.</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="workoutDuration"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Preferred Workout Duration: {field.value} minutes</FormLabel>
              <FormControl>
                <Slider
                  min={15}
                  max={90}
                  step={5}
                  defaultValue={[field.value]}
                  onValueChange={(value) => field.onChange(value[0])}
                />
              </FormControl>
              <FormDescription>Your preferred workout duration in minutes.</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="fitnessLevel"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Fitness Level</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select fitness level" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="beginner">Beginner</SelectItem>
                  <SelectItem value="intermediate">Intermediate</SelectItem>
                  <SelectItem value="advanced">Advanced</SelectItem>
                </SelectContent>
              </Select>
              <FormDescription>Your current fitness level.</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Update goals</Button>
      </form>
    </Form>
  )
}

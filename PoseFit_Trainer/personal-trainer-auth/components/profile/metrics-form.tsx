"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { toast } from "@/hooks/use-toast"

const metricsFormSchema = z.object({
  height: z.string().min(1, {
    message: "Please enter your height.",
  }),
  weight: z.string().min(1, {
    message: "Please enter your weight.",
  }),
  units: z.string({
    required_error: "Please select your preferred units.",
  }),
  bodyFat: z.string().optional(),
  restingHeartRate: z.string().optional(),
})

type MetricsFormValues = z.infer<typeof metricsFormSchema>

export function MetricsForm() {
  const [loading, setLoading] = useState(true);
  
  const form = useForm<MetricsFormValues>({
    resolver: zodResolver(metricsFormSchema),
    defaultValues: {
      height: "",
      weight: "",
      units: "metric",
      bodyFat: "",
      restingHeartRate: "",
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
          
          // Reset form with user data
          form.reset({
            height: data.height?.toString() || "",
            weight: data.weight?.toString() || "",
            units: "metric", // Default to metric
            bodyFat: data.body_metrics?.body_fat?.toString() || "",
            restingHeartRate: data.body_metrics?.resting_heart_rate?.toString() || "",
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

  async function onSubmit(data: MetricsFormValues) {
    try {
      // In a real implementation, you would send this data to your API
      toast({
        title: "Metrics updated",
        description: "Your body metrics have been updated successfully.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update metrics.",
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
          name="units"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Preferred Units</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select units" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="metric">Metric (cm, kg)</SelectItem>
                  <SelectItem value="imperial">Imperial (ft, lbs)</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField
            control={form.control}
            name="height"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Height</FormLabel>
                <FormControl>
                  <Input type="number" step="0.1" {...field} />
                </FormControl>
                <FormDescription>
                  {form.watch("units") === "metric" ? "In centimeters" : "In feet and inches (e.g., 5'10\")"}
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="weight"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Weight</FormLabel>
                <FormControl>
                  <Input type="number" step="0.1" {...field} />
                </FormControl>
                <FormDescription>{form.watch("units") === "metric" ? "In kilograms" : "In pounds"}</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField
            control={form.control}
            name="bodyFat"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Body Fat Percentage (optional)</FormLabel>
                <FormControl>
                  <Input type="number" step="0.1" {...field} />
                </FormControl>
                <FormDescription>Enter as a percentage (e.g., 15)</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="restingHeartRate"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Resting Heart Rate (optional)</FormLabel>
                <FormControl>
                  <Input type="number" {...field} />
                </FormControl>
                <FormDescription>In beats per minute</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
        <Button type="submit">Update metrics</Button>
      </form>
    </Form>
  )
}

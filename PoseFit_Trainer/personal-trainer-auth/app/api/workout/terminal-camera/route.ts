import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';
import { cookies } from 'next/headers';
import fs from 'fs';

// Map of exercise names to their method names in the Python code
const exerciseMethodMap: { [key: string]: string } = {
  'bicep-curls': 'bicep_curls',
  'bicep_curls': 'bicep_curls',
  'push-ups': 'push_ups',
  'push_ups': 'push_ups',
  'squats': 'squats',
  'mountain-climbers': 'mountain_climbers',
  'mountain_climbers': 'mountain_climbers'
};

export async function POST(request: NextRequest) {
  try {
    const data = await request.json();
    const { exercise, sets, reps } = data;

    console.log('Received request with data:', { exercise, sets, reps });

    // Convert exercise name to method name
    const exerciseMethod = exerciseMethodMap[exercise];
    if (!exerciseMethod) {
      console.error('Unsupported exercise:', exercise, 'Available exercises:', Object.keys(exerciseMethodMap));
      return NextResponse.json(
        { 
          error: `Unsupported exercise type: ${exercise}`,
          availableExercises: Object.keys(exerciseMethodMap)
        },
        { status: 400 }
      );
    }

    // Get session token for authentication
    const cookieStore = cookies();
    const sessionToken = await cookieStore.get('session')?.value;

    if (!sessionToken) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }

    // Try multiple possible paths to find the Python script
    const possiblePaths = [
      path.join(process.cwd(), 'AI_PersonTrainer backend', 'AI_PersonTrainer_april_10_4_21', 'run_trainer.py'),
      path.join(process.cwd(), '..', 'AI_PersonTrainer backend', 'AI_PersonTrainer_april_10_4_21', 'run_trainer.py'),
      path.join(process.cwd(), '..', '..', 'AI_PersonTrainer backend', 'AI_PersonTrainer_april_10_4_21', 'run_trainer.py'),
      path.join(process.cwd(), '..', '..', '..', 'AI_PersonTrainer backend', 'AI_PersonTrainer_april_10_4_21', 'run_trainer.py')
    ];

    let scriptPath = null;
    let workingDir = null;

    for (const testPath of possiblePaths) {
      console.log('Trying path:', testPath);
      if (fs.existsSync(testPath)) {
        scriptPath = testPath;
        workingDir = path.dirname(testPath);
        console.log('Found script at:', scriptPath);
        console.log('Working directory:', workingDir);
        break;
      }
    }

    if (!scriptPath || !workingDir) {
      console.error('Script not found in any of the possible locations');
      return NextResponse.json(
        { error: 'Exercise script not found. Please check the installation.' },
        { status: 500 }
      );
    }

    // Get user email from session token (or use default for testing)
    const userEmail = 'test@example.com';

    // Construct command arguments - removed --mode terminal as it's not supported
    const args = [
      scriptPath,
      '--exercise', exerciseMethod,
      '--sets', sets.toString(),
      '--reps', reps.toString(),
      '--user_email', userEmail
    ];

    console.log('Running command:', 'python', args.join(' '));

    // Create a Promise to handle the process execution
    const processPromise = new Promise((resolve, reject) => {
      const pythonProcess = spawn('python', args, {
        cwd: workingDir
      });

      let stdoutData = '';
      let stderrData = '';

      pythonProcess.stdout.on('data', (data) => {
        stdoutData += data.toString();
        console.log(`Python output: ${data}`);
      });

      pythonProcess.stderr.on('data', (data) => {
        stderrData += data.toString();
        console.error(`Python error: ${data}`);
      });

      pythonProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
        if (code !== 0) {
          reject(new Error(`Process failed with code ${code}. Error: ${stderrData}`));
        } else {
          resolve({ code, output: stdoutData });
        }
      });

      pythonProcess.on('error', (error) => {
        console.error('Failed to start Python process:', error);
        reject(error);
      });
    });

    // Wait for process to start (but don't wait for it to finish)
    await Promise.race([
      processPromise,
      new Promise(resolve => setTimeout(resolve, 2000)) // 2 second timeout
    ]).catch(error => {
      console.error('Error during process startup:', error);
      throw error;
    });

    return NextResponse.json({ 
      message: 'Camera workout started',
      scriptPath: scriptPath,
      workingDir: workingDir,
      exercise: exerciseMethod,
      status: 'running'
    });

  } catch (error: unknown) {
    console.error('Error in terminal-camera route:', error);
    return NextResponse.json(
      { 
        error: error.message || 'Internal server error',
        details: error.stack
      },
      { status: 500 }
    );
  }
} 
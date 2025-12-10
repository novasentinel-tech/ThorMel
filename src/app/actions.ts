'use server';

import { spawn } from 'child_process';
import path from 'path';

/**
 * Runs the Python pentest script and streams its output.
 * @param target The target URL or IP address.
 * @param scanType The type of scan to run ('analise' or 'analise_exploracao').
 * @returns A promise that resolves with the JSON report as a string.
 */
export async function runScan(target: string, scanType: string): Promise<string> {
  // Use the absolute path to the Python executable within the virtual environment.
  const pythonExecutable = '/home/user/studio/venv/bin/python3';

  const cybersegurancaDir = path.join(process.cwd(), 'cyberseguranca');
  const scriptName = 'IA_main.py';

  console.log(`[Action] Executing: ${pythonExecutable} ${scriptName} in ${cybersegurancaDir}`);

  return new Promise((resolve, reject) => {
    const pythonProcess = spawn(pythonExecutable, [scriptName, target, scanType], {
      cwd: cybersegurancaDir,
    });

    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
      const chunk = data.toString();
      // console.log(`stdout: ${chunk}`); // Commented out to reduce noise
      stdout += chunk;
    });

    pythonProcess.stderr.on('data', (data) => {
      const chunk = data.toString();
      console.error(`stderr: ${chunk}`);
      stderr += chunk;
    });

    pythonProcess.on('close', (code) => {
      console.log(`child process exited with code ${code}`);
      if (code !== 0) {
        reject(new Error(`Script finalizado com código ${code}:\n${stderr || stdout}`));
        return;
      }

      const marker = '---JSON-REPORT-START---';
      const jsonIndex = stdout.indexOf(marker);

      if (jsonIndex === -1) {
        reject(new Error('JSON não encontrado na saída do script.'));
        return;
      }

      const jsonString = stdout.slice(jsonIndex + marker.length).trim();

      try {
        // Validate that the extracted string is valid JSON
        JSON.parse(jsonString);
        // Resolve with the clean JSON string
        resolve(jsonString);
      } catch (e) {
        reject(new Error(`JSON inválido retornado pelo script: ${(e as Error).message}`));
      }
    });

    pythonProcess.on('error', (err) => {
      console.error('Failed to start subprocess.', err);
      reject(new Error(`Falha ao iniciar o script: ${err.message}`));
    });
  });
}

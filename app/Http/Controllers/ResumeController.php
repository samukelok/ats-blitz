<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Process;
use App\Models\Resume;
use Illuminate\Support\Facades\Log;
use Smalot\PdfParser\Parser; // For PDF parsing
use PhpOffice\PhpWord\IOFactory; // For DOCX parsing
use Illuminate\Support\Facades\Session;

class ResumeController extends Controller
{
    public function showUploadForm()
    {
        return view('upload');
    }

    public function upload(Request $request)
    {
        $request->validate([
            'resume' => 'required|file|mimes:pdf,docx,txt|max:2048',
            'job_title' => 'required|string|max:255' 
        ]);

        try {
            $file = $request->file('resume');
            $path = $file->store('resumes');
            $jobTitle = $request->input('job_title');

            // First, attempt to extract text from the file
            $text = $this->extractText($file, $jobTitle);

            // If text extraction fails, use OCR fallback
            if (!$text) {
                // Log that we are falling back to OCR
                Log::info('Text extraction failed, falling back to OCR processing');

                $fileContent = file_get_contents($file); // Get file content in raw binary form
                $text = $this->runOcrFallback($fileContent, $jobTitle); // Run OCR if text extraction fails

                if (!$text) {
                    throw new \Exception("Could not extract text from the resume. Image-based PDFs not supported.");
                }
            }

            // Now that we have the text (either extracted or via OCR), pass it to Python
            $result = Process::run([
                'python', 
                base_path('ai/resume_analyser.py'), 
                base64_encode($text), 
                base64_encode($jobTitle) 
            ]);

            if ($result->failed()) {
                throw new \Exception("Python script failed: " . $result->errorOutput());
            }

            $analysis = json_decode($result->output(), true);

            if (json_last_error() !== JSON_ERROR_NONE || !isset($analysis['score'])) {
                throw new \Exception("Invalid analysis output");
            }

            // Store job title in the database
            $resume = Resume::create([
                'filename' => $file->getClientOriginalName(),
                'filepath' => $path,
                'job_title' => $jobTitle, 
                'score' => $analysis['score'],
                'feedback' => json_encode($analysis['feedback'])
            ]);

            return redirect()
                ->route('results', $resume->id)
                ->with('success', 'Resume analysed successfully!');

        } catch (\Exception $e) {
            Log::error("Resume processing failed: " . $e->getMessage());
            return back()->withInput()->with('error', 'Error processing resume: ' . $e->getMessage());
        }
    }

    // OCR fallback method to handle image-based PDFs
    protected function runOcrFallback($fileContent, $jobTitle)
    {
        try {
            $encodedFileContent = base64_encode($fileContent); // Encode the PDF file content
            $encodedJobTitle = base64_encode($jobTitle); // Encode the job title

            // Execute the OCR fallback Python script
            $result = Process::run([
                'python3', 
                base_path('ai/ocr_fallback.py'),
                $encodedFileContent,
                $encodedJobTitle
            ]);

            if ($result->failed()) {
                Log::error("OCR fallback failed: " . $result->errorOutput());
                return null; // If OCR fails, return null
            }

            // Return the text extracted via OCR
            return $result->output();

        } catch (\Exception $e) {
            Log::error("OCR fallback execution failed: " . $e->getMessage());
            return null;
        }
    }

    private function extractText($file, $jobTitle = null)
    {
        $extension = $file->getClientOriginalExtension();
        $path = $file->getRealPath();
    
        // Handle PDF files
        if ($extension === 'pdf') {
            // First attempt: Try smalot/pdfparser (fast for text-based PDFs)
            try {
                $parser = new \Smalot\PdfParser\Parser();
                $pdf = $parser->parseFile($path);
                $text = trim($pdf->getText());
    
                if (!empty($text)) {
                    return $text; // Successfully extracted text
                }
            } catch (\Exception $e) {
                \Log::warning("PDF parsing failed: " . $e->getMessage());
            }
    
            // Fallback: Python OCR for image-based PDFs
            try {
                $result = Process::run([
                    'python',
                    base_path('ai/ocr_fallback.py'),
                    base64_encode(file_get_contents($path)),
                    base64_encode($jobTitle ?? '')
                ]);                               
    
                if ($result->failed()) {
                    throw new \Exception("OCR failed: " . $result->errorOutput());
                }
    
                return trim($result->output());
            } catch (\Exception $e) {
                \Log::error("OCR fallback failed: " . $e->getMessage());
                return null;
            }
        }
        // Handle DOCX files (your existing code)
        elseif ($extension === 'docx') {
            $zip = new \ZipArchive;
            if ($zip->open($path) === true) {
                $xmlIndex = 'word/document.xml';
                if (($index = $zip->locateName($xmlIndex)) !== false) {
                    $xmlData = $zip->getFromIndex($index);
                    $zip->close();
                    $text = strip_tags($xmlData);
                    return trim($text);
                }
                $zip->close();
            }
            return null;
        }
    
        return null; // Unsupported file type
    }


    public function showResults($id)
    {
        $resume = Resume::findOrFail($id);
        
        // If no timezone stored, use session or default
        if (!$resume->timezone) {
            $resume->timezone = Session::get('timezone', 'UTC+2');
        }
        
        return view('results', compact('resume'));
    }
}

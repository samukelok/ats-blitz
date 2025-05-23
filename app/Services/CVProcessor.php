<?php

namespace App\Services;

use Smalot\PdfParser\Parser;
use PhpOffice\PhpWord\IOFactory;

class CVProcessor
{
    public function extractText($file)
    {
        $extension = strtolower($file->getClientOriginalExtension());
        
        if ($extension === 'pdf') {
            return $this->extractTextFromPdf($file);
        } elseif (in_array($extension, ['docx', 'doc'])) {
            return $this->extractTextFromWord($file);
        }
        
        throw new \Exception('Unsupported file type. Please upload PDF or Word documents.');
    }

    protected function extractTextFromPdf($file)
    {
        $parser = new Parser();
        $pdf = $parser->parseFile($file->getRealPath());
        return $pdf->getText();
    }

    protected function extractTextFromWord($file)
    {
        $phpWord = IOFactory::load($file->getRealPath());
        $text = '';
        
        foreach ($phpWord->getSections() as $section) {
            foreach ($section->getElements() as $element) {
                if (method_exists($element, 'getText')) {
                    $text .= $element->getText() . ' ';
                }
            }
        }
        
        return trim($text);
    }
}
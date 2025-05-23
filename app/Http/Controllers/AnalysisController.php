<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Resume;

class AnalysisController extends Controller
{
    public function show($id)
    {
        // Retrieve the resume and analysis data by ID
        $resume = Resume::findOrFail($id);

        // Pass the resume data to the view
        return view('results', compact('resume'));
    }
}

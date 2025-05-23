<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;
use App\Http\Controllers\ResumeController;
use App\Http\Controllers\AnalysisController;

Route::get('/analysis/{id}', [AnalysisController::class, 'show'])->name('analysis.show');
Route::get('/', [ResumeController::class, 'showUploadForm'])->name('home');
Route::post('/upload', [ResumeController::class, 'upload'])->name('upload');
Route::get('/results/{id}', [ResumeController::class, 'showResults'])->name('results');
Route::get('/test-timezone', function(Request $request) {
    return response()->json([
        'detected' => $request->input('timezone', 'Not provided'),
        'valid' => in_array($request->input('timezone'), timezone_identifiers_list()),
        'all_timezones' => timezone_identifiers_list()
    ]);
});

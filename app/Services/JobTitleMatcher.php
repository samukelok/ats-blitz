<?php

namespace App\Services;

use App\Models\StandardisedJobTitle;
use App\Models\UnverifiedJobTitle;
use Illuminate\Support\Str;

class JobTitleMatcher
{
    public function analyse(string $cvText, string $jobTitle): array
    {
        $standardisedTitle = $this->standardiseTitle($jobTitle);
        
        // Check if job exists in approved titles
        $isApproved = StandardisedJobTitle::where('standardised_title', $standardisedTitle)->exists();
        
        // Calculate score
        $baseScore = $this->calculateBaseScore($cvText);
        $finalScore = $isApproved ? $baseScore : $baseScore * 0.8;
        
        // Store unverified titles
        if (!$isApproved) {
            UnverifiedJobTitle::firstOrCreate(
                ['original_title' => $jobTitle],
                ['suggested_standardised_title' => $standardisedTitle]
            );
        }
        
        return [
            'score' => round($finalScore),
            'is_approved_job' => $isApproved,
            'original_job_title' => $jobTitle,
            'job_title_used' => $standardisedTitle
        ];
    }

    protected function standardiseTitle(string $title): string
    {
        $existing = StandardisedJobTitle::where('standardised_title', 'like', $title)
                     ->orWhere('original_title', 'like', $title)
                     ->first();
        
        return $existing 
            ? $existing->standardised_title
            : Str::of($title)
                ->rtrim('s')
                ->replaceMatches('/, (except|all other).*/i', '')
                ->toString();
    }

    protected function calculateBaseScore(string $cvText): float
    {
        // Your existing score calculation
        return rand(70, 90); 
    }
}
<?php
// app/Services/JobTitleMatcher.php
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
        
        // If not approved, add to unverified table
        if (!$isApproved) {
            $this->addToUnverified($jobTitle, $standardisedTitle);
        }
        
        // Calculate score with penalty for unapproved jobs
        $baseScore = $this->calculateBaseScore($cvText);
        $finalScore = $isApproved ? $baseScore : $baseScore * 0.8;
        
        return [
            'score' => round($finalScore),
            'is_approved_job' => $isApproved,
            'original_job_title' => $jobTitle,
            'job_title_used' => $standardisedTitle
        ];
    }

    protected function addToUnverified(string $original, string $standardised): void
    {
        UnverifiedJobTitle::firstOrCreate(
            ['original_title' => $original],
            ['suggested_standardised_title' => $standardised]
        );
    }

    protected function standardiseTitle(string $title): string
    {
        return Str::of($title)
            ->rtrim('s')
            ->replaceMatches('/, (except|all other).*/i', '')
            ->toString();
    }

    protected function calculateBaseScore(string $cvText): float
    {
        // Your scoring logic Demo
        return rand(70, 90); 
    }
}
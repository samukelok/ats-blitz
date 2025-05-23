@extends('layouts.app')

@section('content')
<div class="container py-5">
    <div class="row justify-content-center">
        <div class="col-lg-10">
            <div class="card shadow-lg border-0">
                <div class="card-header bg-primary text-white py-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <h4 class="mb-0"><i class="bi bi-file-earmark-text me-2"></i>Resume Analysis Results</h4>
                        <span class="badge bg-white text-primary fs-6">
                            <i class="bi bi-clock-history me-1"></i> 
                            {{ $resume->created_at->setTimezone('Africa/Johannesburg')->format('M j, Y g:i A') }}(UTC+2)
                        </span>
                    </div>
                </div>
                
                <div class="card-body p-4">
                    <div class="row align-items-center mb-4">
                        <div class="col-md-6">
                            <h5 class="mb-1">
                                <i class="bi bi-file-earmark me-2"></i>{{$resume->filename}}
                            </h5>
                            <p class="text-muted mb-0">
                                <small>Last analysed: {{ $resume->updated_at->diffForHumans() }}</small>
                            </p>
                        </div>
                        <div class="col-md-6 text-md-end mt-3 mt-md-0">
                            <div class="display-3 fw-bold 
                                @if($resume->score >= 80) text-success
                                @elseif($resume->score >= 50) text-warning
                                @else text-danger
                                @endif">
                                {{ $resume->score }}<small class="fs-4">/100</small>
                            </div>
                        </div>
                    </div>

                    <!-- Progress Bar with Animated Transition -->
                    <div class="progress mb-4" style="height: 25px;">
                        <div class="progress-bar progress-bar-striped progress-bar-animated
                            @if($resume->score >= 80) bg-success
                            @elseif($resume->score >= 50) bg-warning
                            @else bg-danger
                            @endif" 
                            role="progressbar" 
                            style="width: {{ $resume->score }}%" 
                            aria-valuenow="{{ $resume->score }}" 
                            aria-valuemin="0" 
                            aria-valuemax="100">
                        </div>
                    </div>

                    <div class="row g-4">
                        <!-- Score Breakdown Card -->
                        <div class="col-lg-6">
                            <div class="card h-100 border-0 shadow-sm">
                                <div class="card-header bg-info text-white py-2">
                                    <h5 class="mb-0"><i class="bi bi-speedometer2 me-2"></i>Score Breakdown</h5>
                                </div>
                                <div class="card-body">
                                    @php
                                        $feedback = json_decode($resume->feedback, true);
                                        $breakdown = $feedback['score_breakdown'] ?? [
                                            'sections' => 0,
                                            'metrics' => 0,
                                            'action_verbs' => 0,
                                            'quality' => 0,
                                            'dates' => 0
                                        ];
                                    @endphp
                                    
                                    <ul class="list-group list-group-flush">
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            <span><i class="bi bi-collection me-2"></i>Sections</span>
                                            <span class="badge bg-primary rounded-pill">{{ $breakdown['sections'] }} pts</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            <span><i class="bi bi-graph-up me-2"></i>Metrics</span>
                                            <span class="badge bg-primary rounded-pill">{{ $breakdown['metrics'] }} pts</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            <span><i class="bi bi-lightning-charge me-2"></i>Action Verbs</span>
                                            <span class="badge bg-primary rounded-pill">{{ $breakdown['action_verbs'] }} pts</span>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                        </div>

                        <!-- Suggestions Card -->
                        <div class="col-lg-6">
                            <div class="card h-100 border-0 shadow-sm">
                                <div class="card-header bg-warning text-dark py-2">
                                    <h5 class="mb-0"><i class="bi bi-magic me-2"></i>Suggestions for Improvement</h5>
                                </div>
                                <div class="card-body">
                                    @php
                                        $score = ($feedback['score_breakdown']['sections'] ?? 0) 
                                            + ($feedback['score_breakdown']['metrics'] ?? 0) 
                                            + ($feedback['score_breakdown']['action_verbs'] ?? 0);
                                        $suggestions = $feedback['suggestions'] ?? [];
                                        
                                        //Duplication Handling
                                        $uniqueSuggestions = [];
                                        $headerShown = false;
                                        foreach ($suggestions as $suggestion) {
                                            if (str_starts_with($suggestion, 'Excellent') || 
                                                str_starts_with($suggestion, 'Great') || 
                                                str_starts_with($suggestion, 'Outstanding')) {
                                                if (!$headerShown) {
                                                    $headerShown = true;
                                                    $uniqueSuggestions[] = $suggestion;
                                                }
                                            } else {
                                                $uniqueSuggestions[] = $suggestion;
                                            }
                                        }
                                    @endphp

                                    @if($resume->score < 75)
                                    <ul class="list-group list-group-flush">
                                        @php
                                            // Filter out praise suggestions
                                            $filteredSuggestions = array_filter($suggestions, function($suggestion) {
                                                return !(
                                                    str_starts_with($suggestion, 'Excellent') || 
                                                    str_starts_with($suggestion, 'Great') || 
                                                    str_starts_with($suggestion, 'Outstanding')
                                                );
                                            });
                                        @endphp

                                        @foreach($filteredSuggestions as $suggestion)
                                            <li class="list-group-item">{{ $suggestion }}</li>
                                        @endforeach
                                    </ul>


                                    @else
                                        <div class="alert alert-success mb-3">
                                            @if($resume->score>= 90)
                                                Outstanding! Your resume exceeds ATS optimisation standards.
                                            @elseif($resume->score >= 80)
                                                Excellent resume! It meets most ATS optimisation criteria.
                                            @else
                                                Improve your resume further to enhance ATS compatibility.
                                            @endif
                                        </div>
                                        
                                        <ul class="list-group list-group-flush">
                                            @foreach($uniqueSuggestions as $suggestion)
                                                @if(!str_starts_with($suggestion, 'Excellent') && 
                                                    !str_starts_with($suggestion, 'Great') && 
                                                    !str_starts_with($suggestion, 'Outstanding'))
                                                    <li class="list-group-item">{{ $suggestion }}</li>
                                                @endif
                                            @endforeach
                                        </ul>
                                    @endif
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <!-- AI Opinion -->
                    <div class="col-lg-12" style = 'margin-top: 20px;'>
                        <div class="card h-100 border-0 shadow-sm">
                            <div class="card-header bg-light text-dark py-2">
                                <h5 class="mb-0"><i class="bi bi-magic me-2"></i>AI Opinion</h5>
                            </div>
                            <div class="card-body">
                                @php
                                function formatAiOpinion($text) {
                                    // Normalize line endings
                                    $text = preg_replace("/\r\n|\r/", "\n", $text);

                                    // Split into blocks separated by 2+ newlines
                                    $blocks = preg_split("/\n{2,}/", trim($text));

                                    $formatted = '';

                                    foreach ($blocks as $block) {
                                        $block = trim($block);

                                        // Heading: if it's ONLY a bold line like **Heading**
                                        if (preg_match('/^\*\*(.+?)\*\*$/', $block, $m)) {
                                            $formatted .= "<h5 class='mt-3 mb-1'>" . htmlspecialchars($m[1]) . "</h5>";
                                            continue;
                                        }

                                        // Ordered list (starts with 1.)
                                        if (preg_match('/^1\.\s/', $block)) {
                                            $lines = preg_split('/\n/', $block);
                                            $formatted .= "<ol class='ms-4'>";
                                            foreach ($lines as $line) {
                                                $line = preg_replace('/^\d+\.\s*/', '', $line);
                                                $line = preg_replace('/\*\*(.+?)\*\*/', '<strong>$1</strong>', $line);
                                                $formatted .= "<li>" . htmlspecialchars_decode($line) . "</li>";
                                            }
                                            $formatted .= "</ol>";
                                            continue;
                                        }

                                        // Unordered list
                                        if (preg_match('/^(\*|\+)\s/', $block)) {
                                            $lines = preg_split('/\n/', $block);
                                            $formatted .= "<ul class='ms-4'>";
                                            foreach ($lines as $line) {
                                                $line = preg_replace('/^(\*|\+)\s*/', '', $line);
                                                $line = preg_replace('/\*\*(.+?)\*\*/', '<strong>$1</strong>', $line);
                                                $formatted .= "<li>" . htmlspecialchars_decode($line) . "</li>";
                                            }
                                            $formatted .= "</ul>";
                                            continue;
                                        }

                                        // Bold inside regular paragraphs (like **Clear career goal**: ...)
                                        $block = preg_replace('/\*\*(.+?)\*\*/', '<strong>$1</strong>', $block);

                                        // Normal paragraph
                                        $formatted .= "<p class='mb-2'>" . htmlspecialchars_decode($block) . "</p>";
                                    }

                                    return $formatted;
                                }
                                    
                                    $ai_opinion = $feedback['ai_opinion'] ?? 'No AI opinion available.';
                                @endphp
                                
                                <p>{!! formatAiOpinion($ai_opinion) !!}</p>

                            </div>
            
                        </div>
                    </div>

                    <!-- Action Buttons -->
                    <div class="text-center mt-4">
                        <a href="{{ route('home') }}" class="btn btn-primary">
                            <i class="bi bi-arrow-left me-1"></i> Analyse Another Resume
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
@endsection
@extends('layouts.app')

@section('content')
<div class="container py-4">
    <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-primary text-white py-3">
                    <h4 class="mb-0 text-center">Upload Your Resume</h4>
                </div>
                
                <div class="card-body p-4">
                    <form method="POST" action="{{ route('upload') }}" enctype="multipart/form-data" id="uploadForm">
                        @csrf
                        <div class="mb-4">
                            <label for="resume" class="form-label fw-semibold">
                                <i class="fas fa-file-pdf me-2 text-danger"></i>
                                <i class="fas fa-file-word me-2 text-primary"></i>
                                <i class="fas fa-file-alt me-2 text-dark"></i>
                                Choose Resume (PDF, DOCX, TXT)
                            </label>

                            <input type="hidden" name="timezone" id="timezoneField">

                            <input type="file" class="form-control form-control-lg" name="resume" id="resume" accept=".pdf,.docx,.txt" required>
                            <div class="form-text text-muted">Max size: 2MB • Supported formats: PDF, DOCX, TXT</div>

                            <input type="text" class="form-control form-control-lg mt-2" name="job_title" id="job_title" placeholder="Enter a job you're interested in (e.g. Accountant) " required>
                            
                        </div>

                        <div class="d-grid gap-2">
                            <button type="submit" class="btn btn-primary btn-lg py-2" id="submitBtn">
                                <span id="submitText">Analyse Resume</span>
                                <span id="spinner" class="spinner-border spinner-border-sm d-none" role="status" aria-hidden="true"></span>
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
@endsection

@section('scripts')
<script>
document.getElementById('uploadForm').addEventListener('submit', function() {
    const submitBtn = document.getElementById('submitBtn');
    const submitText = document.getElementById('submitText');
    const jobTitle = document.getElementById('job_title').value;
    const spinner = document.getElementById('spinner');
    
    submitBtn.disabled = true;
    submitText.textContent = "Analyzing...";
    spinner.classList.remove('d-none');
});
</script>

@endsection
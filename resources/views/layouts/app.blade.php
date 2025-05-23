<!DOCTYPE html>
<html lang="en">
<head>  
    <meta charset="UTF-8">      
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>ATS Blitz - Analyse Your Resume</title>
    
    <meta name="csrf-token" content="{{ csrf_token() }}">

    <!-- logo -->
    <link rel="icon" href="{{ asset('./img/ATS_web_logo.png') }}" type="image/png">

    <!-- Bootstrap CSS -->  
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">

    <style>
        .far-right {
        position: absolute;
        right: 0;
        top: 0;
        height: 100%;
        display: flex;
        align-items: center;
        background:  #007bff;
        padding: 0 1.5rem;
        transition: all 0.3s ease;
    }
    
    .far-right a {
        color: white;
        text-decoration: none;
        font-weight: 600;
        font-size: 1rem;
        display: flex;
        align-items: center;
        transition: all 0.2s ease;
        margin-bottom: 2px;
    }
    
    .far-right:hover {
        background: linear-gradient(90deg, rgb(0, 123, 255) 0%, #0069d9 100%);
    }
    
    .far-right a:hover {
        color: #ffffff;
        transform: translateX(3px);
    }
    
    .far-right svg {
        transition: transform 0.2s ease;
        margin-top: 5px;
        margin-left: -5px;
    }
    
    .far-right:hover svg {
        transform: translateX(3px);
    }
    
    </style>
    @stack('styles')
</head>
<body>
    <div id="app">
        <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
            <div class="container">
                <a class="navbar-brand" href="{{ route('home') }}" style = 'font-size: 25px;'>
                    <img src="{{ asset('./img/ATS_web_logo.png') }}" alt="logo" width = '25px' style = 'margin-top: -6px'></i>ATS Blitz
                </a>
            </div>

            <div class="far-right pe-4">
                <a href="https://github.com/samukelok/ats-blitz" class="d-flex align-items-center" target="_blank" rel="noopener noreferrer">
                    <span class="me-1">View Documentation</span>
                    <svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" fill="currentColor" class="bi bi-arrow-right-short" viewBox="0 0 16 16">
                        <path fill-rule="evenodd" d="M4 8a.5.5 0 0 1 .5-.5h5.793L8.146 5.354a.5.5 0 1 1 .708-.708l3 3a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.708-.708L10.293 8.5H4.5A.5.5 0 0 1 4 8z"/>
                    </svg>
                </a>
        </div>
        </nav>

        <main class="py-4">
            <div class="container">
                @if(session('success'))
                    <div class="alert alert-success alert-dismissible fade show">
                        {{ session('success') }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                @endif

                @if(session('error'))
                    <div class="alert alert-danger alert-dismissible fade show">
                        {{ session('error') }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                @endif

                @yield('content')
            </div>
        </main>
    </div>

    <!-- Bootstrap JS Bundle with Popper -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    @stack('scripts')
</body>
</html>
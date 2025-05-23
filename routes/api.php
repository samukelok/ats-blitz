<?php
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use Symfony\Component\Process\Process;

Route::post('/ats/score', [JobMatchController::class, 'match']);
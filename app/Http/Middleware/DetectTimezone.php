<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Session;

class DetectTimezone
{
    public function handle(Request $request, Closure $next)
    {
        // Set timezone from request or session
        if ($request->has('timezone')) {
            Session::put('timezone', $request->input('timezone'));
        } elseif (!Session::has('timezone')) {
            Session::put('timezone', 'UTC');
        }

        return $next($request);
    }
}
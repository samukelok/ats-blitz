<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Resume extends Model
{
    protected $fillable = ['filename', 'filepath', 'job_title', 'score', 'feedback'];

    protected $casts = [
        'feedback' => 'array', 
    ];
}

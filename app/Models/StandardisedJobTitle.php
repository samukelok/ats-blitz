<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class StandardisedJobTitle extends Model
{
    protected $guarded = [];
    
    public function scopeApproved($query)
    {
        return $query->where('is_approved', true);
    }
    
    public function scopeNeedsReview($query)
    {
        return $query->where('is_approved', false);
    }
}
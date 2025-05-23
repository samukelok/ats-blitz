<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('standardised_job_titles', function (Blueprint $table) {
            $table->id();
            $table->string('original_code', 20)->unique();
            $table->string('original_title');
            $table->string('standardised_title');
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('standardised_job_titles');
    }
};
